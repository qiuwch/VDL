/*
 * The Spread Toolkit.
 *     
 * The contents of this file are subject to the Spread Open-Source
 * License, Version 1.0 (the ``License''); you may not use
 * this file except in compliance with the License.  You may obtain a
 * copy of the License at:
 *
 * http://www.spread.org/license/
 *
 * or in the file ``license.txt'' found in this distribution.
 *
 * Software distributed under the License is distributed on an AS IS basis, 
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
 * for the specific language governing rights and limitations under the 
 * License.
 *
 * The Creators of Spread are:
 *  Yair Amir, Michal Miskin-Amir, Jonathan Stanton, John Schultz.
 *
 *  Copyright (C) 1993-2006 Spread Concepts LLC <info@spreadconcepts.com>
 *
 *  All Rights Reserved.
 *
 * Major Contributor(s):
 * ---------------
 *    Ryan Caudy           rcaudy@gmail.com - contributions to process groups.
 *    Claudiu Danilov      claudiu@acm.org - scalable wide area support.
 *    Cristina Nita-Rotaru crisn@cs.purdue.edu - group communication security.
 *    Theo Schlossnagle    jesus@omniti.com - Perl, autoconf, old skiplist.
 *    Dan Schoenblum       dansch@cnds.jhu.edu - Java interface.
 *
 */


#include <string.h>
#include <stdio.h>
#include <assert.h>
#include "membership.h"
#include "spread_params.h"
#include "flow_control.h"
#include "prot_body.h"
#include "net_types.h"
#include "network.h"
#include "objects.h"
#include "memory.h"
#include "status.h"
#include "alarm.h"

#define		POTENTIAL_REP	0
#define		SEG_REP		1
#define		RING_REP	2

typedef	struct	dummy_members_info{
	int16		num_members;
	int16		num_pending;
	int32		members[MAX_PROCS_RING];
} members_info;

typedef	struct	dummy_rep_info{
	int32		proc_id;
	int16		type;
	int16		seg_index;
} rep_info;

typedef	struct	dummy_reps_info{
	int16		num_reps;
	int16		rep_index;
	rep_info	reps[MAX_REPS];
} reps_info;

typedef struct	dummy_ring_info{
	membership_id	memb_id;
        int32           trans_time;
	int32		aru;
	int32		highest_seq;
	int32		num_holes;
	int16		num_commit;
	int16		num_trans;
} ring_info;

static	configuration	Membership;
static	membership_id	Membership_id;
static	configuration	Future_membership;
static	membership_id	Future_membership_id;

static  membership_id   Trans_memb_id;
static  int32           F_trans_memb_time;
static  int32           Last_time_used;

static	int		State;
static	int		Token_alive;
static  proc            My;
static	int32		My_seg_rep;
static	int		Foreign_found;
static	configuration	*Cn;

static	members_info	F_members;
static	reps_info	F_reps;
static	reps_info	Potential_reps;

static	members_info	Commit_set;
static	members_info	Future_commit_set;

static	sys_scatter	Send_pack;

static	sp_time		Zero_timeout 	= {  0, 0};

static	void	Memb_handle_alive  ( sys_scatter *scat );
static	void	Memb_handle_join   ( sys_scatter *scat );
static	void	Memb_handle_refer  ( sys_scatter *scat );
static	void	Memb_handle_foreign( sys_scatter *scat );
static	void	Memb_handle_form1  ( sys_scatter *scat );
static	void	Memb_handle_form2  ( sys_scatter *scat );
static	void	Shift_to_seg();
static	void	Gather_or_represented();
static	void	Shift_to_gather();
static	void	Shift_to_represented();
static	void	Form_or_fail();
static	void	Scast_alive();
static	void	Send_join();
static	int	Insert_member( members_info *m, int32 proc_id );
static	int	Insert_rep( reps_info *r, rep_info rep );
static	int32	Smallest_member( members_info *m, int *index );
static	int32	Smallest_rep( reps_info *r, int *index );
static	void	Sort_members( members_info *m );
static	void	Sort_reps( reps_info *r );
static	void	Create_form1();
static	void	Fill_form1( sys_scatter *scat );
static	void	Read_form2( sys_scatter *scat );
static	void	Backoff_membership();
static	void	Flip_members( members_info *members_ptr );
static	void	Flip_reps( reps_info *reps_ptr );
static	void	Flip_rings( char *buf );

void		Memb_init()
{
	packet_header	*pack_ptr;
	int32		reference_subnet;
	int32		current_subnet;
	int		i, num_seg;

	State = OP;
	GlobalStatus.state = OP;
	GlobalStatus.membership_changes = 0;

	My = Conf_my();
	Cn = Conf_ref();
        num_seg = Conf_num_segments( Cn );

	reference_subnet = Cn->segments[0].procs[0]->id;
	reference_subnet = reference_subnet & 0xffff0000;

	Wide_network = 0;
	for( i=1; i < num_seg; i++ )
	{
		current_subnet = Cn->segments[i].procs[0]->id;
		current_subnet = current_subnet & 0xffff0000;
		if( current_subnet != reference_subnet )
		{
			Wide_network = 1;
			break;
		}
	}

	if( Wide_network )
	{
		Token_timeout.sec  =  20; Token_timeout.usec  = 0;
		Hurry_timeout.sec  =   6; Hurry_timeout.usec  = 0;

		Alive_timeout.sec  =   1; Alive_timeout.usec  = 0;
		Join_timeout.sec   =   1; Join_timeout.usec   = 0;
		Rep_timeout.sec    =   5; Rep_timeout.usec    = 0;
		Seg_timeout.sec    =   2; Seg_timeout.usec    = 0;
		Gather_timeout.sec =  10; Gather_timeout.usec = 0;
		Form_timeout.sec   =  10; Form_timeout.usec   = 0;
		Lookup_timeout.sec =  90; Lookup_timeout.usec = 0;
	}else{
		Token_timeout.sec  =   5; Token_timeout.usec  = 0;
		Hurry_timeout.sec  =   2; Hurry_timeout.usec  = 0;

		Alive_timeout.sec  =   1; Alive_timeout.usec  = 0;
		Join_timeout.sec   =   1; Join_timeout.usec   = 0;
		Rep_timeout.sec    =   2; Rep_timeout.usec    = 500000;
		Seg_timeout.sec    =   2; Seg_timeout.usec    = 0;
		Gather_timeout.sec =   5; Gather_timeout.usec = 0;
		Form_timeout.sec   =   5; Form_timeout.usec   = 0;
		Lookup_timeout.sec =  60; Lookup_timeout.usec = 0;
	}

        /* Lookup timeout when only one segment exists can be longer,
         * since a no remote segments need to be probed
         */
        if ( num_seg == 1 )
            Lookup_timeout.sec = 300;

	Membership = Conf();
	for( i=0; i < num_seg; i++ )
		Membership.segments[i].num_procs = 0;
        Conf_append_id_to_seg( &Membership.segments[My.seg_index], My.id);
	Membership_id.proc_id = My.id;
	Membership_id.time    = -1;
        Last_time_used        = Membership_id.time;
	Transitional	      = 0;
	Reg_membership    = Membership;

	pack_ptr = new(PACK_HEAD_OBJ);
	pack_ptr->proc_id = My.id;

	Send_pack.elements[0].len = sizeof(packet_header);
	Send_pack.elements[0].buf = (char *)pack_ptr;

	Memb_token_loss();
}

void    Memb_signal_conf_reload(void)
{
        My = Conf_my();

}
configuration	*Memb_active_ptr()
{
	if( State == EVS ) return ( &Future_membership );
	else return( &Membership );
}

membership_id	Memb_id()
{
	return( Membership_id );
}

membership_id   Memb_trans_id()
{
        return( Trans_memb_id );
}

int	Memb_is_equal( membership_id m1, membership_id m2 )
{
	if( m1.proc_id == m2.proc_id && m1.time == m2.time )
		return( 1 );
	else
		return( 0 );
}

int32	Memb_state()
{
	return( State );
}

int	Memb_token_alive()
{ 
	return( Token_alive );
}

void	Memb_handle_message( sys_scatter *scat )
{
	packet_header	*pack_ptr;

	pack_ptr = (packet_header *)scat->elements[0].buf;

	if( 	  Is_alive( pack_ptr->type ) )
	{
		Alarm( MEMB, "Memb_handle_message: handling alive message\n");
		Memb_handle_alive( scat );

	}else if( Is_join( pack_ptr->type ) ){
		Alarm( MEMB, "Memb_handle_message: handling join message from %d.%d.%d.%d, State is %d\n", 
                       IP1(pack_ptr->proc_id),
                       IP2(pack_ptr->proc_id),
                       IP3(pack_ptr->proc_id),
                       IP4(pack_ptr->proc_id),
                       State);
		Memb_handle_join( scat );

	}else if( Is_refer( pack_ptr->type ) ){
		Alarm( MEMB, "Memb_handle_message: handling refer message from %d.%d.%d.%d, State is %d\n",
                       IP1(pack_ptr->proc_id),
                       IP2(pack_ptr->proc_id),
                       IP3(pack_ptr->proc_id),
                       IP4(pack_ptr->proc_id),
                       State);
		Memb_handle_refer( scat );

	}else if( Is_regular( pack_ptr->type ) ){
		Alarm( NONE, "Memb_handle_message: handling foreign message from %d.%d.%d.%d, State is %d\n",
                       IP1(pack_ptr->proc_id),
                       IP2(pack_ptr->proc_id),
                       IP3(pack_ptr->proc_id),
                       IP4(pack_ptr->proc_id),
                       State);
		Memb_handle_foreign( scat );

	}else{
		Alarm( EXIT, "Memb_handle_message: unknown message type %d\n",
			pack_ptr->type );

	}
} 

void	Memb_handle_token( sys_scatter *scat )
{
	token_header	*token_ptr;

	token_ptr = (token_header *)scat->elements[0].buf;

	if( 	  Is_form1( token_ptr->type ) )
	{
		Alarm( MEMB, "Memb_handle_token: handling form1 token\n");
		Memb_handle_form1( scat );

	}else if( Is_form2( token_ptr->type ) ){
		Alarm( MEMB, "Memb_handle_token: handling form2 token\n");
		Memb_handle_form2( scat );

	}else{
		Alarm( EXIT, "Memb_handle_token: unknown token type %d\n",
			token_ptr->type );

	}
} 

static	void	Memb_handle_alive( sys_scatter *scat )
{
	packet_header	*pack_ptr;

    pack_ptr 	= (packet_header *)scat->elements[0].buf;

    switch( State )
    {
	case OP:
	    Alarm( MEMB, "Handle_alive in OP\n");
	    if( Conf_id_in_conf( &Membership, pack_ptr->proc_id ) != -1 )
	    {
		/* sender belongs to my ring - my token is lost */
		Memb_token_loss();
		/* update my F_members list */
		Insert_member( &F_members, pack_ptr->proc_id );
	    }
	    break;

	case SEG:
	    Alarm( MEMB, "Handle_alive in SEG\n");
	    /* update my F_members list */
	    Insert_member( &F_members, pack_ptr->proc_id );

	    break;

	case REPRESENTED:
	    Alarm( MEMB, "Handle_alive in REPRESENTED\n");
	    E_queue( Shift_to_seg, 0, NULL, Rep_timeout );

	    break;

	case GATHER:
	    Alarm( MEMB, "Handle_alive in GATHER\n");
	    /*
	     * If I am a seg representative - take this guy 
	     * If I am a ring leader: if this guy in my ring - lost token
	     *			      otherwise ignore.
	     */
	    if( ! Token_alive ) Insert_member( &F_members, pack_ptr->proc_id );
	    else if( Conf_id_in_conf( &Membership, pack_ptr->proc_id ) != -1 ){
		/* sender belongs to my ring - my token is lost */
		Memb_token_loss();
		/* update my F_members list */
		Insert_member( &F_members, pack_ptr->proc_id );
	    }
	    break;

	case FORM:
	    /* 
	     * Ignore. 
	     * In principle if this guy is in my formed membership 
	     * then I know I lost the token, but there is no way
	     * to know at this time if this guy is in my formed memb.
	     */	 

	    break;

	case EVS:
	    /* 
	     * If this guy in my formed membership then my token is lost 
	     * Otherwise ignore
	     */
	    if( Conf_id_in_conf( &Future_membership, pack_ptr->proc_id ) != -1 )
	    {
		Memb_token_loss();
		/* update my F_members list */
		Insert_member( &F_members, pack_ptr->proc_id );
	    }
	    break;
	}
}

static	void	Memb_handle_join( sys_scatter *scat )
{
	packet_header	*pack_ptr;
	members_info	*members_ptr;
	reps_info	*reps_ptr;
	packet_header	refer_pack;
	sys_scatter	send_scat;
	proc		p;
	int		i;
	int		ret;
	int		dummy;

    pack_ptr 	= (packet_header *) scat->elements[0].buf;
    members_ptr = (members_info  *) scat->elements[1].buf;

    if( !Same_endian( pack_ptr->type ) ) Flip_members( members_ptr );

    i =	2*sizeof(int16) + (members_ptr->num_members)*sizeof(int32);
    reps_ptr	= (reps_info     *)&scat->elements[1].buf[i];

    if( !Same_endian( pack_ptr->type ) ) Flip_reps( reps_ptr );

    switch( State )
    {
	case OP:
	    /* if sender belongs to my ring then my token is lost (except for single segment confs)
	       otherwise if I am a ring leader shift_to_gather */
	    Alarm( MEMB, "Handle_join in OP\n");
	    if( Conf_id_in_conf( &Membership, pack_ptr->proc_id ) == -1 )
	    {
		if( Conf_leader( &Membership ) == My.id ) 
		{
			Potential_reps.reps[0] = reps_ptr->reps[0];
			Potential_reps.num_reps = 1;
			F_members.num_members = 0;
			F_members.num_pending = 0;
			Shift_to_gather();
		}else{
			/* if !from my_seg OR seg_leader - answer ref */
			if( reps_ptr->reps[0].seg_index != My.seg_index ||
			    Conf_seg_leader( &Membership, My.seg_index) == My.id )
			{
			    refer_pack.type            = REFER_TYPE;
			    refer_pack.proc_id         = My.id;
			    refer_pack.memb_id.proc_id = Conf_leader( &Membership );
			    refer_pack.memb_id.time    = RING_REP;
			    refer_pack.data_len	       = 0;
			    send_scat.num_elements     = 1;
			    send_scat.elements[0].buf  = (char *)&refer_pack;
			    send_scat.elements[0].len  = sizeof(packet_header);
			    Net_ucast( pack_ptr->proc_id, &send_scat );
			}
		}
	    }else{
	        /* sender belongs to my ring - my token is lost */
                /* If only one segment exists, then token is not lost, but rather
                 * a JOIN probe for merged segments was received. This can be
                 * ignored because a real token loss will trigger an ALIVE broadcast
                 * packet which will force the membership change.
                 */
                if ( Conf_num_segments( Cn ) > 1 )
                    Memb_token_loss();
	    }
	    break;

	case SEG:
	    ret = Conf_proc_by_id( pack_ptr->proc_id, &p );
	    if( My.seg_index == p.seg_index && 
		reps_ptr->reps[0].type == SEG_REP)
	    {
		/* this guy is my representative */
		My_seg_rep = pack_ptr->proc_id;
		Shift_to_represented();
		for( i=0; i < members_ptr->num_members; i++ )
		    if( members_ptr->members[i] == My.id ) break;
		Scast_alive( 1 );
	    }else{
		/* no need to remember this join */
	    }
	    break;

	case REPRESENTED:
	    ret = Conf_proc_by_id( pack_ptr->proc_id, &p );
	    if( My.seg_index == p.seg_index && 
		reps_ptr->reps[0].type == SEG_REP)
	    {
		if( pack_ptr->proc_id != My_seg_rep )
		{
		    Alarm( MEMB, 
			"Memb_handle_join: representative shifts: old %d, new %d\n",
			My_seg_rep, pack_ptr->proc_id );
		    My_seg_rep = pack_ptr->proc_id;
		}
		E_queue( Shift_to_seg, 0, NULL, Rep_timeout );
		for( i=0; i < members_ptr->num_members; i++ )
		    if( members_ptr->members[i] == My.id ) break;
		Scast_alive( 1 );
	    }else{
		/* if My_seg_rep is determined -  send it to this guy */
		/* My_seg_rep can be undetermined if it did not issue a join yet */
		if( My_seg_rep != -1 )
		{
			/* send my_seg_rep to pack_ptr->proc_id */
			refer_pack.type            = REFER_TYPE;
			refer_pack.proc_id         = My.id;
			refer_pack.memb_id.proc_id = My_seg_rep;
			refer_pack.memb_id.time    = SEG_REP;
			refer_pack.data_len	   = 0;
			send_scat.num_elements     = 1;
			send_scat.elements[0].buf  = (char *)&refer_pack;
			send_scat.elements[0].len  = sizeof(packet_header);
			Net_ucast( pack_ptr->proc_id, &send_scat );
		}
	    }
	    break;

	case GATHER:
	    /* update my F_reps list */
	    Insert_rep( &F_reps, reps_ptr->reps[0] );
	    for( i=0; i < reps_ptr->num_reps; i++ )
	    {
		Insert_rep( &Potential_reps, reps_ptr->reps[i] );
	    }
	    /* if sender is my Smallest rep - advance Gather_timeout */
	    if( Smallest_rep( &F_reps, &dummy ) ==  reps_ptr->reps[0].proc_id )
		E_queue( Form_or_fail, 0, NULL, Gather_timeout );

	    break;

	case FORM:
	    /* Ignore */

	    break;

	case EVS:
	    /* 
	     * If this guy in my formed membership then my token is lost 
	     * Otherwise ignore
	     */
	    if( Conf_id_in_conf( &Future_membership, pack_ptr->proc_id ) != -1 )
	    {
		Memb_token_loss();
		/* update my F_members list */
		Insert_member( &F_members, pack_ptr->proc_id );
	    }
	    break;
	}
}

static	void	Memb_handle_refer( sys_scatter *scat )
{
	packet_header	*pack_ptr;
	proc		p;
	rep_info	temp_rep;
	int		ret;

    pack_ptr 	= (packet_header *) scat->elements[0].buf;

    switch( State )
    {
	case OP:
	    Alarm( MEMB, "Handle_refer in OP\n");
		break;

	case SEG:
	    Alarm( MEMB, "Handle_refer in SEG\n");
		break;

	case REPRESENTED:
	    Alarm( MEMB, "Handle_refer in REPRESENTED\n");
		break;

	case GATHER:
	    Alarm( MEMB, "Handle_refer in GATHER\n");
		ret = Conf_proc_by_id( pack_ptr->memb_id.proc_id, &p );
		if( ret < 0 )
		{
			Alarm( PRINT, "Memb_handle_refer: unknown proc_id %d\n",
				pack_ptr->memb_id.proc_id );
			return;
		}
		temp_rep.proc_id   = p.id;
		temp_rep.type      = pack_ptr->memb_id.time;
		temp_rep.seg_index = p.seg_index;
		Insert_rep( &Potential_reps, temp_rep );
		break;

	case FORM:
	    Alarm( MEMB, "Handle_refer in FORM\n");
		break;

	case EVS:
	    Alarm( MEMB, "Handle_refer in EVS\n");
		break;

    }
}

static	void	Memb_handle_foreign( sys_scatter *scat )
{
	packet_header	*pack_ptr;
	proc		p;
	int		ret;

    pack_ptr 	= (packet_header *) scat->elements[0].buf;

    switch( State )
    {
	case OP:
	    Alarm( NONE, "Handle_foreign in OP\n");
		ret = Conf_proc_by_id( pack_ptr->proc_id, &p );
		if( ret < 0 )
		{
			Alarm( PRINT, "Memb_handle_foreign: unknown proc_id %d\n",
				pack_ptr->proc_id );
			return;
		}
		if( Conf_leader( &Membership ) == My.id )
		{
			Memb_lookup_new_members();
		}else if( Conf_seg_leader( &Membership, My.seg_index ) == My.id &&
			  (!Foreign_found) ){
			/*
			 * Seg leader : sending one foreign message
			 * to Conf leader 
			 */
			sys_scatter		send_scat;

			Foreign_found = 1;
			send_scat.num_elements = 2;
			send_scat.elements[0].buf = scat->elements[0].buf;
			send_scat.elements[0].len = scat->elements[0].len;
			send_scat.elements[1].buf = scat->elements[1].buf;
			send_scat.elements[1].len = pack_ptr->data_len;
			
			Net_ucast( Conf_leader( &Membership ), &send_scat );
			Net_ucast( Conf_leader( &Membership ), &send_scat );
		}
		break;

	case SEG:
	    Alarm( NONE, "Handle_foreign in SEG\n");
		break;

	case REPRESENTED:
	    Alarm( NONE, "Handle_foreign in REPRESENTED\n");
		break;

	case GATHER:
	    Alarm( NONE, "Handle_foreign in GATHER\n");
		break;

	case FORM:
	    Alarm( NONE, "Handle_foreign in FORM\n");
		break;

	case EVS:
	    Alarm( NONE, "Handle_foreign in EVS\n");
		/* 
		 * This may happen when multiple old memberships merge 
		 * and a message is retransmitted using bcast or scast.
		 * i.e. more than one proc miss it and another proc recieves it
		 */
		break;

    }
}

static	void	Memb_handle_form1( sys_scatter *scat )
{
    switch( State )
    {
	case OP:
	    Alarm( MEMB, "Handle_form1 in OP\n");
		if( Conf_leader( &Membership ) == My.id ) /* do nothing */;
		else Fill_form1( scat );
		break;

	case SEG:
	    Alarm( MEMB, "Handle_form1 in SEG\n");
		/* swallow this token */
		break;

	case REPRESENTED:
	    Alarm( MEMB, "Handle_form1 in REPRESENTED\n");
		Fill_form1( scat );
		break;

	case GATHER:
	    Alarm( MEMB, "Handle_form1 in GATHER\n");
		Fill_form1( scat );
		break;

	case FORM:
	    Alarm( MEMB, "Handle_form1 in FORM\n");
		/* swallow this token */
		break;

	case EVS:
	    Alarm( MEMB, "Handle_form1 in EVS\n");
		/* swallow this token */
		break;

    }
}

static	void	Memb_handle_form2( sys_scatter *scat )
{
    switch( State )
    {
	case OP:
		Alarm( MEMB, "Handle_form2 in OP\n");
		/* swallow this token */
		break;

	case SEG:
		Alarm( MEMB, "Handle_form2 in SEG\n");
		/* swallow this token */
		break;

	case REPRESENTED:
		Alarm( MEMB, "Handle_form2 in REPRESENTED\n");
		/* swallow this token */
		break;

	case GATHER:
		Alarm( MEMB, "Handle_form2 in GATHER\n");
		/* swallow this token */
		break;

	case FORM:
		Alarm( MEMB, "Handle_form2 in FORM\n");
		Read_form2( scat );
		break;

	case EVS:
		Alarm( MEMB, "Handle_form2 in EVS\n");
		/* swallow this token */
		break;
    }
}

void	Memb_token_loss()
{
	rep_info	temp_rep;
	int		i;

    switch( State )
    {
	case OP:
	    /* my token is lost - shift to seg */

	    Commit_set.num_members = 1;
	    Commit_set.members[0] = My.id;

	    Potential_reps.num_reps = 0;
	    temp_rep.type = POTENTIAL_REP;
	    for( i=0; i < Conf_num_segments( Cn ); i++ )
	    {
		if( i == My.seg_index ) continue;
		temp_rep.seg_index = i;
		if( Membership.segments[i].num_procs > 0 )
		{
			temp_rep.proc_id = Membership.segments[i].procs[0]->id;
		}else{
			temp_rep.proc_id = Conf_seg_leader( Cn, i );
		}
		Insert_rep( &Potential_reps, temp_rep );
	    }
	    break;

	case SEG:
	case REPRESENTED:
	    Alarm( EXIT, "Memb_token_loss: bug !!! state is %d\n",State);

	    break;

	case GATHER:
	    /* I think I totally solved it */
	    /* If I am not a ring leader it is a bug */
	    if( ! Token_alive )
		Alarm( EXIT, "Memb_token_loss: bug !!! state is %d\n",State);

	    /* I am a ring leader and I lost my ring */
	    Commit_set.num_members = 1;
	    Commit_set.members[0] = My.id;

	    Potential_reps.num_reps = 0;
	    temp_rep.type = POTENTIAL_REP;

	    /* First adding reps that I gathered - they are more important */
	    /* starting from 1 not to include myself!! */
	    for( i=1; i < F_reps.num_reps; i++ )
	    {
		temp_rep = F_reps.reps[i];
		Insert_rep( &Potential_reps, temp_rep );
	    }

	    /* Next adding reps from my membership - they are less important */
	    for( i=0; i < Conf_num_segments( Cn ); i++ )
	    {
		if( i == My.seg_index ) continue;
		temp_rep.seg_index = i;
		if( Membership.segments[i].num_procs > 0 )
		{
			temp_rep.proc_id = Membership.segments[i].procs[0]->id;
		}else{
			temp_rep.proc_id = Conf_seg_leader( Cn, i );
		}
		Insert_rep( &Potential_reps, temp_rep );
	    }
	    break;

	case FORM:
	    /* my token is lost - shift to seg */
	    /* potential already updated according to form token */
	    break;

	case EVS:
	    /* my token is lost - shift to seg */
	    /* clear empty messages */
	    Backoff_membership();

	    /* update potential according to future_membership */
	    Potential_reps.num_reps = 0;
	    temp_rep.type = POTENTIAL_REP;
	    for( i=0; i < Conf_num_segments( Cn ); i++ )
	    {
		if( i == My.seg_index ) continue;
		temp_rep.seg_index = i;
		if( Future_membership.segments[i].num_procs > 0 )
		{
			temp_rep.proc_id = 
				Future_membership.segments[i].procs[0]->id;
		}else{
			temp_rep.proc_id = Conf_seg_leader( Cn, i );
		}
		Insert_rep( &Potential_reps, temp_rep );
	    }
	    break;
    }
    Alarm( MEMB, "Memb_token_loss: I lost my token, state is %d\n",State);
    Shift_to_seg();

    Token_alive = 0;
    E_dequeue( Memb_token_loss,    0, NULL );
    E_dequeue( Send_join,	   0, NULL );
    E_dequeue( Form_or_fail,	   0, NULL );
    E_dequeue( Prot_token_hurry,   0, NULL );
    E_dequeue( Memb_lookup_new_members, 0, NULL );
    Last_token->type = 0;
    Last_token->seq  = 0;
    Last_token->aru  = 0;

    for( i=0; i < Conf_num_segments( Cn ); i++ )
	Membership.segments[i].num_procs = 0;
    Conf_append_id_to_seg(&Membership.segments[My.seg_index], My.id);
}

static	void	Shift_to_seg()
{
	State = SEG;
	GlobalStatus.state = SEG;

	F_members.num_members = 1;
	F_members.members[0] = My.id;
	F_members.num_pending = 0;
	E_queue( Scast_alive, 0, NULL, Zero_timeout );
	E_queue( Gather_or_represented,  0, NULL, Seg_timeout );
}

static	void	Gather_or_represented()
{
	int	dummy;

	My_seg_rep = -1;

	if( Smallest_member( &F_members, &dummy ) ==  My.id )
	{
		Shift_to_gather();
	}else{
		Shift_to_represented();
	}
}

static	void	Shift_to_gather()
{
	State = GATHER;
	GlobalStatus.state = GATHER;

	F_reps.num_reps 	 = 1;
	F_reps.reps[0].proc_id 	 = My.id;
	F_reps.reps[0].seg_index = My.seg_index;
	if( Token_alive )
		F_reps.reps[0].type = RING_REP;
	else	F_reps.reps[0].type = SEG_REP;

	E_dequeue( Scast_alive,        0, NULL );
	E_dequeue( Memb_lookup_new_members, 0, NULL );
	E_queue( Send_join,    0, NULL, Zero_timeout );
	E_queue( Form_or_fail, 0, NULL, Gather_timeout );
}

static	void	Shift_to_represented()
{
	State = REPRESENTED;
	GlobalStatus.state = REPRESENTED;

	E_dequeue( Scast_alive, 0, NULL );
	E_dequeue( Gather_or_represented, 0, NULL );
	E_queue( Shift_to_seg, 0, NULL, Rep_timeout );
}

static	void	Form_or_fail()
{

	rep_info	temp_rep;
	int		i;
	int		dummy;

	if( Smallest_rep( &F_reps, &dummy ) ==  My.id )
	{
		if( Token_alive && F_reps.num_reps == 1 )
		{
			/* clear everything and go back to op */
			E_dequeue( Send_join, 0, NULL);
			E_queue( Memb_lookup_new_members, 0, NULL, Lookup_timeout );
			State = OP;
			GlobalStatus.state = OP;
		}else{
			/* create and send form token */
			Create_form1();
		}
	}else{
		if( Token_alive )
		{
			/* clear everything and go back to op */
			Alarm( MEMB, "Form_or_fail:failed, return to OP\n");
			E_dequeue( Send_join, 0, NULL );
			E_queue( Memb_lookup_new_members, 0, NULL, Lookup_timeout );
			State = OP;
			GlobalStatus.state = OP;
		}else{
			Alarm( MEMB, "Form_or_fail: failed to gather\n");
			/* failed to gather again */
			F_members.num_members = 1;
			F_members.members[0] = My.id;
			F_members.num_pending = 0;
			
	    		Potential_reps.num_reps = 0;
	    		temp_rep.type = POTENTIAL_REP;
			/* starting from 1 not to include myself!! */
			for( i=1; i < F_reps.num_reps; i++ )
			{
				temp_rep = F_reps.reps[i];
				Insert_rep( &Potential_reps, temp_rep );
			}

			Shift_to_gather();
		}
	}
}

static	void	Scast_alive( int code, void *dummy )
{
	packet_header	*pack_ptr;

	Alarm( MEMB, "Scast_alive: State is %d\n", State);

	pack_ptr = (packet_header *)Send_pack.elements[0].buf;
	pack_ptr->type = ALIVE_TYPE;
	pack_ptr->data_len = 
		2*sizeof(int16) + (F_members.num_members)*sizeof(int32);

	Send_pack.elements[1].buf = (char *)&F_members;
	Send_pack.elements[1].len = pack_ptr->data_len;
	Send_pack.num_elements = 2;
	Net_scast( My.seg_index, &Send_pack );
	if( code == 0 )
		E_queue( Scast_alive, 0, NULL, Alive_timeout );
}

static	void	Send_join()
{
	packet_header	*pack_ptr;
	int		i;

	Alarm( MEMB, "Send_join: State is %d\n", State);

	pack_ptr = (packet_header *)Send_pack.elements[0].buf;
	pack_ptr->type = JOIN_TYPE;
	Send_pack.elements[1].buf = (char *)&F_members;
	Send_pack.elements[1].len = 
		2*sizeof(int16) + (F_members.num_members)*sizeof(int32);
	Send_pack.elements[2].buf = (char *)&F_reps;
	Send_pack.elements[2].len = 
		2*sizeof(int16) + (F_reps.num_reps)*sizeof(rep_info);
	Send_pack.num_elements = 3;

	pack_ptr->data_len = Send_pack.elements[1].len + Send_pack.elements[2].len;

	if( !Token_alive )
	{
		Net_scast( My.seg_index, &Send_pack );
	}
	for( i=0; i < Potential_reps.num_reps; i++ )
	{
		Net_ucast( Potential_reps.reps[i].proc_id, &Send_pack );
	}

	E_queue( Send_join, 0, NULL, Join_timeout );
}

void	Memb_lookup_new_members()
{
	packet_header	*pack_ptr;
	int		num_missing;
	int		i,j;

	if( State != OP )
	{
		Alarm( MEMB, "Memb_lookup_new_member: not in OP state, returning\n");
		return;
	}

	Potential_reps.num_reps = 0;

	F_reps.num_reps		= 1;
	F_reps.reps[0].proc_id	= My.id;
	F_reps.reps[0].seg_index= My.seg_index;
	F_reps.reps[0].type	= RING_REP;
	F_members.num_members = 0;
	F_members.num_pending = 0;

	pack_ptr = (packet_header *)Send_pack.elements[0].buf;
	pack_ptr->type = JOIN_TYPE;
	Send_pack.elements[1].buf = (char *)&F_members;
	Send_pack.elements[1].len = 
		2*sizeof(int16) + (F_members.num_members)*sizeof(int32);
	Send_pack.elements[2].buf = (char *)&F_reps;
	Send_pack.elements[2].len = 
		2*sizeof(int16) + (F_reps.num_reps)*sizeof(rep_info);
	Send_pack.num_elements = 3;

	pack_ptr->data_len = Send_pack.elements[1].len + Send_pack.elements[2].len;

	num_missing = 0;
        /* For single segment configured, send local broadcast of join to entire segment -- current members will ignore */
        if ( Conf_num_segments( Cn ) == 1 ) {
            Net_scast( My.seg_index, &Send_pack );
            num_missing++;
        } else {
            /* Send unicasts to each host that is not in the current membership. */
            for( i=0; i < Conf_num_segments( Cn ); i++ )
            {
		for( j=0; j < Conf_num_procs_in_seg( Cn, i ); j++ )
		{
		    if( Conf_id_in_conf( &Reg_membership, Cn->segments[i].procs[j]->id ) == -1 )
		    {
			Net_ucast( Cn->segments[i].procs[j]->id, &Send_pack );
			num_missing++;
		    }
		}
            }
        }
	if( num_missing ) Shift_to_gather();
}

static	int	Insert_member( members_info *m, int32 proc_id )
{
	int 	i;

	for( i=0; i < m->num_members; i++ )
	    if( m->members[i] == proc_id )
	    {
		return( 0 );
	    }

       if (m->num_members == MAX_PROCS_RING) 
       {
            /* members structure is full -- so we ignore this new member */
            Alarmp( SPLOG_WARNING, MEMB, "Insert_member: members structure full (%u members) so ignore new member (ID %u.%u.%u.%u)\n", m->num_members, IP1(proc_id), IP2(proc_id), IP3(proc_id), IP4(proc_id) );
            return( 0 );
        }
	m->members[m->num_members] = proc_id;
	m->num_members++;
	return( 1 );
}

static	int	Insert_rep( reps_info *r, rep_info rep )
{
	proc	p;
	int	ret;
	int 	i;

	ret = Conf_proc_by_id( rep.proc_id, &p );
	if( ret < 0 ) 
		Alarm( EXIT, "Insert_rep: proc %d not exist\n", rep.proc_id );

	if( rep.type == POTENTIAL_REP )
	{
	    /* when Potential - if there is someone from same segment (of any type RING, SEG, POTENTIAL
               - don't insert */
	    for( i=0; i < r->num_reps; i++ )
	    {
		if( r->reps[i].seg_index == p.seg_index )
		{
			return( 0 );
		}
	    }
	}else if( rep.type == SEG_REP ) {
	    /* 
             * when Seg - if there is other SEG or RING from same segment - keep all.
             * if it is POTENTIAL then replace it and exit because no other from this segment can exist.
             */
	    for( i=0; i < r->num_reps; i++ )
	    {
		if( r->reps[i].seg_index == p.seg_index )
		{
		    if( r->reps[i].type == POTENTIAL_REP )
		    {
			r->reps[i].type = SEG_REP;
			r->reps[i].proc_id = p.id;
			return( 1 );
		    }else if( r->reps[i].type == SEG_REP ) {
                        if (r->reps[i].proc_id == p.id )
                                return( 0 );
		    }else if( r->reps[i].type == RING_REP && 
			      r->reps[i].proc_id == p.id ) {
			/* Former RING_REP lost its ring and became SEG_REP */
		    	r->reps[i].type = SEG_REP;
			return( 1 );
		    }
		}
	    }
	}else if( rep.type == RING_REP ) {
 	    /* 
             * when Ring - if it exists exactly (proc_id) - make it from ring, 
             * in any case elminate potentials.
             * If potential exists, it is known that no ring or seg exists.
             */
	    for( i=0; i < r->num_reps; i++ )
	    {
                if( r->reps[i].seg_index == p.seg_index )
		{
		    if( r->reps[i].type == POTENTIAL_REP )
		    {
			r->reps[i].type = RING_REP;
			r->reps[i].proc_id = p.id;
			return( 1 );
                    }else if( r->reps[i].type == SEG_REP ) {
                        if (r->reps[i].proc_id == p.id ) {
                                r->reps[i].type = RING_REP;
                                return( 1 );
                        }
		    }else if( r->reps[i].type == RING_REP && 
			      r->reps[i].proc_id == p.id ) {
			return( 0 );
                    }
		}
	    }
	}else Alarm( EXIT, "Insert_rep: unknown rep.type %d \n", rep.type );

        if (r->num_reps == MAX_REPS) 
        {
            /* reps structure is full -- so we ignore this new rep */
            Alarmp( SPLOG_WARNING, MEMB, "Insert_rep: reps structure full (%u reps) so ignore new rep (Type %d SegIndex %u ID %u.%u.%u.%u)\n", r->num_reps, rep.type, rep.seg_index, IP1(rep.proc_id), IP2(rep.proc_id), IP3(rep.proc_id), IP4(rep.proc_id) );
            return( 0 );
        }
	r->reps[r->num_reps] = rep;
	r->num_reps++;
	return( 1 );
}

static	int32	Smallest_member( members_info *m, int *index )
{
	int	current;
	int	i;
	proc	curr_proc, i_proc;
	int	ret;

	current = 0;
	ret = Conf_proc_by_id( m->members[current], &curr_proc );
	if( ret < 0 ) Alarm( EXIT, "Smallest_member: unknown proc_id %d\n",
				m->members[current] );
	for( i=1; i < m->num_members; i++ )
	{
		ret = Conf_proc_by_id( m->members[i], &i_proc );
		if( ret < 0 ) Alarm( EXIT, 
			"Smallest_member: Bug! i: %d, proc %d\n",
			i, m->members[i] );
		if( i_proc.seg_index < curr_proc.seg_index  ||
		    ( i_proc.seg_index   == curr_proc.seg_index &&
		      i_proc.index_in_seg < curr_proc.index_in_seg ) )
		{
			curr_proc = i_proc;
			current = i;
		}
	}
	*index = current;
	return( m->members[current] );
}

static	int32	Smallest_rep( reps_info *r, int *index )
{
	int	current;
	int	i;
	proc	curr_p, i_p;
	int	ret;

	current = 0;
	for( i=1; i < r->num_reps; i++ )
	{
		if( r->reps[current].type == SEG_REP )
		{
		    if( r->reps[i].type == SEG_REP )
		    {
			if( r->reps[i].seg_index < r->reps[current].seg_index )
				current = i;
		    }
		}else if( r->reps[current].type == RING_REP ) {
		    if( r->reps[i].type == RING_REP )
		    {
			if( r->reps[i].seg_index < r->reps[current].seg_index )
				current = i;
			else if( r->reps[i].seg_index == r->reps[current].seg_index )
			{
			    ret = Conf_proc_by_id( r->reps[current].proc_id, &curr_p );
			    ret = Conf_proc_by_id( r->reps[i].proc_id, &i_p );
			    if( i_p.index_in_seg < curr_p.index_in_seg )
				current = i;
			}
		    }else if( r->reps[i].type == SEG_REP ){
			current = i;
		    }

		}else Alarm( EXIT, 
			"Smallest_rep: bug! current index %d is proc %d of type %d\n",
			current,r->reps[current].proc_id,r->reps[current].type );
	}
	*index = current;
	return ( r->reps[current].proc_id );
}

static	void	Sort_members( members_info *m )
{
	members_info	temp_members;
	int		index;
	int		i;
	int32		dummy;

	temp_members = *m;
	for( i=0; i < m->num_members; i++ )
	{
		dummy = Smallest_member( &temp_members, &index );
		m->members[i] = temp_members.members[index];
		temp_members.num_members--;
		temp_members.members[index] = 
			temp_members.members[temp_members.num_members];
	}
}

static	void	Sort_reps( reps_info *r )
{
	reps_info	temp_reps;
	int		index;
	int		i;
	int32		dummy;

	temp_reps = *r;

	for( i=0; i < r->num_reps; i++ )
	{
		dummy = Smallest_rep( &temp_reps, &index );
		r->reps[i] = temp_reps.reps[index];
		temp_reps.num_reps--;
		temp_reps.reps[index] = temp_reps.reps[temp_reps.num_reps];
	}
}

static	void	Create_form1()
{
	token_header	form_token;
	ring_info	*rg_info;
	int32		*num_rings;
	int32		*holes_procs_ptr;
	int32		index;
	int		pack_entry;
	int		num_bytes;
	sys_scatter	send_scat;
	char		rg_info_buf[sizeof(token_body)];
	rep_info	temp_rep;
	int		i,j;
        int             cur_num_members;
        members_info    valid_members;

	form_token.seq = Highest_seq+3333;
	form_token.proc_id = My.id;
	form_token.type = FORM1_TYPE;

	/* if I am a ring leader - update my F_members */
	if( F_reps.reps[0].type == RING_REP )
	{
		F_members.num_members = 0;
		for( i=0; i < Membership.num_segments; i++ )
		    for( j=0; j < Membership.segments[i].num_procs; j++ )
		    {
			F_members.members[F_members.num_members] =
				Membership.segments[i].procs[j]->id;
			F_members.num_members++;
		    }
	}
        
        cur_num_members = 0;
        for ( i = 0; i < F_members.num_members; i++ ) {
            int invalid_member;
            invalid_member = 0;
            
            /* Remove from F_members any members that are also in OUR F_reps (except myself). */
            for ( j = 0; j < F_reps.num_reps; j++ ) {
                if ( (F_members.members[i] == F_reps.reps[j].proc_id ) && 
                     (F_members.members[i] != My.id) ) {
                    invalid_member = 1;
                    break;
                }
            }
            if (!invalid_member) {
                valid_members.members[cur_num_members] = F_members.members[i];
                cur_num_members++;
            }
        }
        memcpy( &F_members.members[0], &valid_members.members[0], cur_num_members * sizeof(int32) );
        F_members.num_members = cur_num_members;

	/* I am the first in F_members. put the rest in pending */
	F_members.num_pending = F_members.num_members - 1;
	F_members.num_members = 1;

	Sort_reps( &F_reps );
	F_reps.rep_index = 1;
	/* update potential in case of failure */
	Potential_reps.num_reps = 0;
	for( i=0; i < F_reps.num_reps; i++ )
	{
		temp_rep = F_reps.reps[i];
		if( temp_rep.seg_index != My.seg_index )
		{
			temp_rep.type = POTENTIAL_REP;
			Insert_rep( &Potential_reps, temp_rep );
		}
	}

	num_bytes = 0;
	num_rings = (int32 *)rg_info_buf;
	*num_rings= 1;
	num_bytes += sizeof(int32);
	rg_info	  = (ring_info *)&rg_info_buf[num_bytes];
	num_bytes += sizeof(ring_info);
	holes_procs_ptr = (int32 *)&rg_info_buf[num_bytes];

	rg_info->memb_id	= Membership_id;
        rg_info->trans_time     = 0;
	rg_info->aru		= Aru;
	rg_info->highest_seq	= Highest_seq;

	/* update holes */
	rg_info->num_holes	= 0;
	for( index = My_aru+1; index <= Highest_seq; index++ )
	{
	    pack_entry = index & PACKET_MASK;
	    if( ! Packets[pack_entry].exist )
	    {
		*holes_procs_ptr = index;
		Alarm( MEMB ,
		    "INSERT HOLE 1 IS %d My_aru is %d, Highest_seq is %d\n",
		    index,My_aru, Highest_seq);
		holes_procs_ptr++;
		num_bytes += sizeof(int32);
		rg_info->num_holes++;
	    }
	}

	/* update commit-trans procs */

	/* insert self in trans and commit */
	rg_info->num_commit	= 1;
	rg_info->num_trans	= 1;
	*holes_procs_ptr = My.id;
	num_bytes += sizeof(int32);
	holes_procs_ptr++;

	/* insert other members of commit set */
	for( i=0; i < Commit_set.num_members; i++ )
	{
		/* skipping self, because already there */
		if( Commit_set.members[i] == My.id ) continue;

		/* insert this member */
		*holes_procs_ptr = Commit_set.members[i];
		holes_procs_ptr++;
		num_bytes += sizeof(int32);
		rg_info->num_commit++;
	}
	
	send_scat.num_elements = 4;
	send_scat.elements[0].buf = (char *)&form_token;
	send_scat.elements[0].len = sizeof(token_header);
	send_scat.elements[1].buf = (char *)&F_members;
	send_scat.elements[1].len = sizeof(members_info);
	send_scat.elements[2].buf = (char *)&F_reps;
	send_scat.elements[2].len = sizeof(reps_info);
	send_scat.elements[3].buf = rg_info_buf;
	send_scat.elements[3].len = num_bytes;

	form_token.rtr_len = send_scat.elements[1].len + send_scat.elements[2].len + 
			      send_scat.elements[3].len;

	/* compute whom to send to */
	if( F_members.num_pending > 0 )
	{
		/* send to next member in pending list */
		Net_ucast_token( F_members.members[F_members.num_members], 
			   &send_scat );
		Net_ucast_token( F_members.members[F_members.num_members], 
			   &send_scat );
	}else if( F_reps.rep_index < F_reps.num_reps){
		/* send to next rep */
		Net_ucast_token( F_reps.reps[F_reps.rep_index].proc_id, &send_scat );
		Net_ucast_token( F_reps.reps[F_reps.rep_index].proc_id, &send_scat );
	}else{
		/* singleton membership */
		F_members.num_pending = 1;
		F_members.num_members = 0;
		form_token.type = FORM2_TYPE;
		send_scat.elements[2].len = sizeof(membership_id);
		form_token.rtr_len = send_scat.elements[1].len +
			send_scat.elements[2].len + send_scat.elements[3].len;
		Net_ucast_token( My.id, &send_scat );
	}

	E_dequeue( Send_join, 0, NULL );
	E_queue( Memb_token_loss, 0, NULL, Form_timeout );
    	E_dequeue( Prot_token_hurry, 0, NULL );
	Token_alive = 0;

	State = FORM;
	GlobalStatus.state = FORM;
}

static	void	Fill_form1( sys_scatter *scat )
{
	sys_scatter	send_scat;
	token_header	*form_token;
	members_info	*m_info;
	reps_info	*r_info;
	ring_info	*old_rg_info, *new_rg_info;
	ring_info	*my_rg_info;
	int32		*old_num_rings, *new_num_rings;
	int32		*my_holes_procs_ptr, *new_holes_procs_ptr;
	int32		index;
	int		pack_entry;
	char		rg_info_buf[sizeof(token_body)];
	char		*c_ptr;
	char		*rings_buf;
	int		num_bytes;
	int		bytes_to_copy;
	rep_info	temp_rep;
	int		i,j,k;
	int             cur_num_members;
        int             num_to_copy;
        members_info    valid_members;
	
	num_bytes  = 0;

	form_token = (token_header *)scat->elements[0].buf;

	m_info	   = (members_info *)scat->elements[1].buf;
	num_bytes  += sizeof(members_info);

	r_info	   = (reps_info    *)&scat->elements[1].buf[num_bytes];
	num_bytes  += sizeof(reps_info);

	rings_buf  = &scat->elements[1].buf[num_bytes];
	old_num_rings  = (int32        *)&scat->elements[1].buf[num_bytes];
	num_bytes  += sizeof(int32);

	old_rg_info= (ring_info    *)&scat->elements[1].buf[num_bytes];

	if( !Same_endian( form_token->type ) )
	{
		Flip_members( m_info );
		Flip_reps( r_info );
		Flip_rings( rings_buf );	
	}

	/* update header */
	form_token->proc_id = My.id;
	if( form_token->seq < Highest_seq+3333 ) form_token->seq = Highest_seq+3333;

	/* update members and reps */
	if( State == OP || State == REPRESENTED )
	{
		/* validity check */
		if( m_info->members[m_info->num_members] != My.id ||
		    m_info->num_pending <= 0 ) return;

		m_info->num_members++;
		m_info->num_pending--;

	}else if( State == GATHER ){

		/* validity check */
		if( r_info->reps[r_info->rep_index].proc_id != My.id ||
		    m_info->num_pending != 0 ) 
		{
			return;
		}

                /*
                 * Add validation check to my F_members list. I need to remove members:
                 *      1) Any members already in the m_info I just received in form1.
                 *      2) Any members of r_info I just received in form1 (except myself).
                 *      3) Any members that are also in OUR F_reps (except myself).
                 *              The reason for this is that these guys also became seg_reps
                 *              from the same segment as me, but did not make it to the final reps list on form1
                 *              and if included as members will act as seg_reps which they should not.
                 */
                cur_num_members = 0;
                for ( i = 0; i < F_members.num_members; i++ ) {
                        int invalid_member;
                        invalid_member = 0;

                        /* 1) Any members already in the m_info I just received in form1. */
                        for ( j = 0; j < m_info->num_members; j++ ) {
                                if (F_members.members[i] == m_info->members[j] ) {
                                        invalid_member = 1;
                                        break;
                                }
                        }

                        /* 2) Any members of r_info I just received in form1 (except myself). */
                        for ( j = 0; !invalid_member && j < r_info->num_reps; j++ ) {
                                if ( (F_members.members[i] == r_info->reps[j].proc_id ) && 
                                     (F_members.members[i] != My.id) ) {
                                        invalid_member = 1;
                                        break;
                                }
                        }

                        /* 3) Any members that are also in OUR F_reps (except myself). */
                        for ( j = 0; !invalid_member && j < F_reps.num_reps; j++ ) {
                                if ( (F_members.members[i] == F_reps.reps[j].proc_id ) && 
                                     (F_members.members[i] != My.id) ) {
                                        invalid_member = 1;
                                        break;
                                }
                        }
                        if (!invalid_member) {
                                valid_members.members[cur_num_members] = F_members.members[i];
                                cur_num_members++;
                        }
                }
                memcpy( &F_members.members[0], &valid_members.members[0], cur_num_members * sizeof(int32) );
                F_members.num_members = cur_num_members;

                /* Now add all my members into the form1 token */
		if( r_info->reps[r_info->rep_index].type == SEG_REP )
		{
			/* Fill myself and my members */
			i = m_info->num_members;
			for( j=0; j < F_members.num_members; j++, i++ )
				m_info->members[i] = F_members.members[j];
			m_info->num_pending = F_members.num_members - 1;
			m_info->num_members += 1; 

		}else if( r_info->reps[r_info->rep_index].type == RING_REP ){
			
			/* Fill myself and my ring members */
			i = m_info->num_members;
			for( j=0; j < Membership.num_segments; j++ )
			    for( k=0; k < Membership.segments[j].num_procs; k++, i++ )
				m_info->members[i] = 
					Membership.segments[j].procs[k]->id;
			m_info->num_pending = i - m_info->num_members -1;
			m_info->num_members += 1;
		}else Alarm( EXIT, "Fill_form1: invalid rep type: %d\n",
			r_info->reps[r_info->rep_index].type );

		r_info->rep_index++;

	}else Alarm( EXIT, "Fill_form1: invalid State: %d\n",State );

	/* update potential in case of failure */
	Potential_reps.num_reps = 0;
	for( i=0; i < r_info->num_reps; i++ )
	{
		temp_rep = r_info->reps[i];
		if( temp_rep.seg_index != My.seg_index )
		{
			temp_rep.type = POTENTIAL_REP;
			Insert_rep( &Potential_reps, temp_rep );
		}
	}


	/* update rings info */
	num_bytes = 0;
	new_num_rings = (int32 *)&rg_info_buf[num_bytes];
	*new_num_rings = 0;
	num_bytes += sizeof(int32);

	my_rg_info = NULL;
	my_holes_procs_ptr = NULL; /* optimiser thinks it may be used
				     uninitialised (its wrong, but it
				     is too subtle for it) */
	for( i=0; i < *old_num_rings; i++ )
	{
	    bytes_to_copy = sizeof(ring_info) +
			( old_rg_info->num_holes + old_rg_info->num_commit )* sizeof(int32);
	    if( Memb_is_equal( old_rg_info->memb_id, Membership_id ) )
	    {
		my_rg_info = old_rg_info;
		c_ptr = (char *) old_rg_info;
		my_holes_procs_ptr = (int32 *)&c_ptr[sizeof(ring_info)];
                old_rg_info = (ring_info *)&c_ptr[bytes_to_copy];
	    }else{
		new_rg_info= (ring_info    *)&rg_info_buf[num_bytes];
		memmove((char *)new_rg_info, (char *)old_rg_info, bytes_to_copy );
		c_ptr = (char *) old_rg_info;
		old_rg_info = (ring_info *)&c_ptr[bytes_to_copy];
		num_bytes   += bytes_to_copy;
		(*new_num_rings)++;
	    }
	}

	new_rg_info= (ring_info    *)&rg_info_buf[num_bytes];
	num_bytes += sizeof(ring_info);
	(*new_num_rings)++;

	new_rg_info->memb_id	 = Membership_id;
        new_rg_info->trans_time  = 0;
	new_rg_info->num_holes	 = 0;
	new_holes_procs_ptr      = (int32 *)&rg_info_buf[num_bytes];

	new_rg_info->aru	 = Aru;
	new_rg_info->highest_seq = Highest_seq;

	if( my_rg_info == NULL )
	{

            if ( *new_num_rings > MAX_FORM_REPS ) 
            {
                /* This ring_info entry will NOT fit in the FORM token packet.
                 * So since the ring_info is needed for me (this daemon) to be
                 * included in the current membership ring, we will have
                 * to remove ourselves from the m_info list and not
                 * create this ring_info 
                 */
                Alarmp( SPLOG_WARNING, MEMB, "Fill_form1: ring_info entry for %u.%u.%u.%u will not fit in FORM token. Removing self from current membership attempt by removing IP from m_info list\n", IP1(My.id), IP2(My.id), IP3(My.id), IP4(My.id));
                /* since new ring is always at the end, we just decrease current byte count */
                num_bytes = num_bytes - sizeof(ring_info);
                (*new_num_rings)--;

                /* Remove ourselves from m_info */
                for ( i=0; i < m_info->num_members; i++) 
                {
                    if( m_info->members[i] == My.id )
                    {
                        num_to_copy = m_info->num_members + m_info->num_pending - i - 1;
                        memmove(&m_info->members[i], &m_info->members[i+1], num_to_copy * sizeof(int32));
                        break;
                    }
                }
                m_info->num_members--;

            } else {
                /* New ring_info will fit, so create it */
                for( index = Last_discarded+1; index <= Highest_seq; index++ )
                {
                    pack_entry = index & PACKET_MASK;
                    if( ! Packets[pack_entry].exist )
                    {
			*new_holes_procs_ptr = index;
			Alarm( MEMB , "INSERT HOLE 2 IS %d\n",index);
			new_holes_procs_ptr++;
			num_bytes     += sizeof(int32);
			new_rg_info->num_holes++;
                    }
                }

                /* update commit-trans procs */

                /* insert self in trans and commit */
                new_rg_info->num_commit	= 1;
                new_rg_info->num_trans	= 1;
                *new_holes_procs_ptr = My.id;
                new_holes_procs_ptr++;
                num_bytes += sizeof(int32);

                /* insert other members of commit set */
                for( i=0; i < Commit_set.num_members; i++ )
                {
                    /* skipping self, because already there */
                    if( Commit_set.members[i] == My.id ) continue;

                    /* insert this member */
                    *new_holes_procs_ptr = Commit_set.members[i];
                    new_holes_procs_ptr++;
                    num_bytes += sizeof(int32);
                    new_rg_info->num_commit++;
                }
            }
	}else{
	
	    members_info temp_set;

	    if( my_rg_info->aru         > Aru )
		new_rg_info->aru 	= my_rg_info->aru;

	    if( my_rg_info->highest_seq > Highest_seq )
		new_rg_info->highest_seq= my_rg_info->highest_seq;

	    for( i=0; i < my_rg_info->num_holes; i++ )
	    {
		pack_entry = *my_holes_procs_ptr & PACKET_MASK;
		if( ! Packets[pack_entry].exist )
		{
			*new_holes_procs_ptr	= *my_holes_procs_ptr;
			Alarm( MEMB ,
		"INSERT HOLE 3 IS %d My_aru is %d, Highest_seq is %d\n",
				*new_holes_procs_ptr,My_aru, Highest_seq);
			new_holes_procs_ptr++;
			num_bytes	+= sizeof(int32);
			new_rg_info->num_holes++;
		}
		my_holes_procs_ptr++;
	    }

	    if( my_rg_info->highest_seq < Highest_seq )
            {
		for( index = my_rg_info->highest_seq+1; 
			index <= Highest_seq; index++ )
		{
		    pack_entry = index & PACKET_MASK;
		    if( ! Packets[pack_entry].exist )
		    {
			Alarm( MEMB , "INSERT HOLE 4 IS %d\n",index);
			*new_holes_procs_ptr = index;
			new_holes_procs_ptr++;
			num_bytes     += sizeof(int32);
			new_rg_info->num_holes++;
		    }
		} 
            }
	    /* setting temp_set to be trans members only */
	    temp_set.num_members = 0;
	    for( i = 0; i < my_rg_info->num_trans; i++ )
	    {
		Insert_member( &temp_set, *my_holes_procs_ptr);
		my_holes_procs_ptr++;
	    }

	    /* creating an updated temp_set based on my_rg_info and Commit_set */

	    /* adding self to trans members */
	    Insert_member( &temp_set, My.id );
	    if( temp_set.num_members != (my_rg_info->num_trans + 1) )
		Alarm( EXIT, "Fill_form1: incorrect trans set\n");
	    temp_set.num_pending = my_rg_info->num_trans+1;

	    /* adding rest of original commit set */
	    for( i = my_rg_info->num_trans; i < my_rg_info->num_commit; i++ )
	    {
		Insert_member( &temp_set, *my_holes_procs_ptr );
		my_holes_procs_ptr++;
	    }

	    /* adding my commit set */
	    for( i = 0; i < Commit_set.num_members; i++ )
	    {
		Insert_member( &temp_set, Commit_set.members[i] );
	    }
	
	    /* writing my ring commit and trans information to new_rg_info */
	    new_rg_info->num_commit = temp_set.num_members;
	    new_rg_info->num_trans  = temp_set.num_pending;
	    for( i = 0; i < temp_set.num_members; i++ )
	    {
		*new_holes_procs_ptr = temp_set.members[i];
		new_holes_procs_ptr++;
		num_bytes += sizeof(int32);
	    }
	}

	send_scat.num_elements = 4;
	send_scat.elements[0].buf = (char *)form_token;
	send_scat.elements[0].len = sizeof(token_header);
	send_scat.elements[1].buf = (char *)m_info;
	send_scat.elements[1].len = sizeof(members_info);
	send_scat.elements[2].buf = (char *)r_info;
	send_scat.elements[2].len = sizeof(reps_info);
	send_scat.elements[3].buf = rg_info_buf;
	send_scat.elements[3].len = num_bytes;

	form_token->rtr_len = send_scat.elements[1].len + send_scat.elements[2].len + 
			      send_scat.elements[3].len;

	/* compute whom to send to */
	if( m_info->num_pending > 0 )
	{
		/* send to next member in pending list */
		Net_ucast_token( m_info->members[m_info->num_members], 
			&send_scat );
		Net_ucast_token( m_info->members[m_info->num_members], 
			&send_scat );
	}else if( r_info->rep_index < r_info->num_reps){
		/* send to next rep */
		Net_ucast_token( r_info->reps[r_info->rep_index].proc_id, 
			&send_scat );
		Net_ucast_token( r_info->reps[r_info->rep_index].proc_id, 
			&send_scat );
	}else{
		/* prepare form2 token */
		Sort_members( m_info );
		m_info->num_pending = m_info->num_members;
		m_info->num_members = 0;
		form_token->type = FORM2_TYPE;
		/* this is the only difference between form1 and form2 tokens */
		send_scat.elements[2].len = sizeof(membership_id);
		form_token->rtr_len = send_scat.elements[1].len + 
				send_scat.elements[2].len + send_scat.elements[3].len;
		Net_ucast_token( m_info->members[0], &send_scat );
		Net_ucast_token( m_info->members[0], &send_scat );
	}

	E_dequeue( Send_join, 0, NULL );
	E_dequeue( Form_or_fail, 0, NULL );
	E_dequeue( Shift_to_seg, 0, NULL );
	E_queue( Memb_token_loss, 0, NULL, Form_timeout );
    	E_dequeue( Prot_token_hurry, 0, NULL );
	Token_alive = 0;

	State = FORM;
	GlobalStatus.state = FORM;
}	

static	void	Read_form2( sys_scatter *scat )
{
	sys_scatter	send_scat;
	token_header	*form_token;
	members_info	*m_info;
	membership_id	*m_id_info;
	ring_info	*rg_info;
	ring_info	*my_rg_info;
	int32		*my_holes_procs_ptr;
	int32		*num_rings;
	int		pack_entry;
	char		*c_ptr;
	char		*rings_buf;
	int		num_bytes;
	int		bytes_to_skip;
	proc		p;
	int		ret;
	int		i;
        int32           memb_time = 0;
	
	num_bytes  = 0;

	form_token = (token_header *)scat->elements[0].buf;

	m_info	   = (members_info *)scat->elements[1].buf;
	num_bytes  += sizeof(members_info);

	m_id_info   = (membership_id *)&scat->elements[1].buf[num_bytes];
	num_bytes  += sizeof(membership_id);

	rings_buf  = &scat->elements[1].buf[num_bytes];
	num_rings  = (int32        *)&scat->elements[1].buf[num_bytes];
	num_bytes  += sizeof(int32);

	rg_info= (ring_info    *)&scat->elements[1].buf[num_bytes];

	if( !Same_endian( form_token->type ) )
	{
		Flip_members( m_info );
		m_id_info->proc_id = Flip_int32( m_id_info->proc_id );
		m_id_info->time    = Flip_int32( m_id_info->time );
		Flip_rings( rings_buf );	
	}

	form_token->proc_id = My.id;

	/* validity check */
	if( m_info->members[m_info->num_members] != My.id ||
	    m_info->num_pending <= 0 ) return;

	m_info->num_members++;
	m_info->num_pending--;

	Last_seq = form_token->seq;

	if( m_info->num_members == 1 )
	{
                /* The time in memb_time is saved to use on one of the
                 * Trans_memb_ids (there is one per Trans_membership view).
                 * The time for the real membership id will be one past
                 * the one in memb_time, because I want time to go forward.
                 */
                memb_time = E_get_time().sec;
                if( memb_time <= Last_time_used )
                        memb_time = Last_time_used + 1;
                Last_time_used = memb_time;

		/* I am future leader, fill membership_id */
		m_id_info->proc_id = My.id;
		m_id_info->time    = ++Last_time_used;
	}

	/* build Future membership and Future membership id */
	Future_membership_id.proc_id = m_id_info->proc_id;
	Future_membership_id.time    = m_id_info->time;
	Future_membership = Conf();
	for( i=0; i < Future_membership.num_segments; i++ )
		Future_membership.segments[i].num_procs = 0;
	for( i=0; i < (m_info->num_members + m_info->num_pending); i++ )
	{
		ret = Conf_proc_by_id( m_info->members[i], &p );
		if( ret < 0 ) Alarm( EXIT, "Read_form2: no such id %u\n",
				m_info->members[i] );
                if ( Conf_append_id_to_seg( &Future_membership.segments[p.seg_index], p.id) == -1)
                        Alarm( EXIT, "Read_form2: BUG2 no such id %u\n", p.id);
	}
	Net_set_membership( Future_membership );
	FC_new_configuration( );

	/* get my ring info */
	my_rg_info = NULL;
	my_holes_procs_ptr = NULL;
	for( i=0; i < *num_rings; i++ )
	{
	    bytes_to_skip = sizeof(ring_info) +
			    ( rg_info->num_holes + rg_info->num_commit ) * sizeof(int32);
	    if( Memb_is_equal( rg_info->memb_id, Membership_id ) )
	    {
		my_rg_info = rg_info;
		my_holes_procs_ptr = 
		    (int32 *)&scat->elements[1].buf[num_bytes+sizeof(ring_info)];
	    }
	    c_ptr = (char *) rg_info;
	    rg_info = (ring_info *)&c_ptr[bytes_to_skip];
	    num_bytes   += bytes_to_skip;
	}

        if (my_rg_info == NULL) {
                Alarm(EXIT, "Read_form2: num_rings = %d, num_bytes = %d, Memb_id = (%d %d)\n",
                      *num_rings, num_bytes, Membership_id.proc_id, Membership_id.time); 
        }

	Highest_seq = my_rg_info->highest_seq;
	Aru	    = my_rg_info->aru;
        /* Note: this call to Discard_packets handles delivery of all the messages
         *       from the old membership with sequence numbers prior to the old Aru.
         */
	Discard_packets();
	
	for( i=0; i < my_rg_info->num_holes; i++ )
	{
		/* create dummy messages */
		pack_entry = *my_holes_procs_ptr & PACKET_MASK;
		Alarm( MEMB , "EXTRACT HOLE IS %d\n",*my_holes_procs_ptr);
		if( Packets[pack_entry].exist != 0 )
		    Alarm( EXIT, "Read_form2: seq %d should be a hole, but is %d\n",
			*my_holes_procs_ptr, Packets[pack_entry].exist );
		Packets[pack_entry].exist = 3;
		my_holes_procs_ptr++;
	}

	/* extract future commit set (and future trans membership) */
	Future_commit_set.num_members = my_rg_info->num_commit;
	Future_commit_set.num_pending = my_rg_info->num_trans;
	for( i=0; i < my_rg_info->num_commit; i++ )
	{
		Future_commit_set.members[i] = *my_holes_procs_ptr;
		my_holes_procs_ptr++;
	}

        /* The token circulates in conf order, which also defines the order
         * by which we choose "leaders."  So, if noone else has set the id
         * for my ring, I get to, and I'll be leader. */
        if( !my_rg_info->trans_time )
        {
                /* memb_time could be already set, if this daemon is the
                 * future leader */
                if( !memb_time )
                {
                        memb_time = E_get_time().sec;
                        if( memb_time <= Last_time_used )
                                memb_time = Last_time_used + 1;
                        Last_time_used = memb_time;
                }
                my_rg_info->trans_time = memb_time;
        }
        F_trans_memb_time = my_rg_info->trans_time;

	send_scat.num_elements = 2;
	send_scat.elements[0].buf = scat->elements[0].buf;
	send_scat.elements[0].len = sizeof(token_header);
	send_scat.elements[1].buf = scat->elements[1].buf;
	send_scat.elements[1].len = num_bytes;

	if( Conf_last( &Future_membership ) != My.id )
	{
		Net_send_token( &send_scat );
		Net_send_token( &send_scat );
		Token_rounds = 0;

	}else{
		/* build first regular token */
		send_scat.num_elements = 1;

		form_token->type = 0;
		form_token->seq = 0;
		form_token->aru = Last_seq;
		form_token->flow_control = 0;
		form_token->rtr_len = 0;

		Net_send_token( &send_scat );
		Token_rounds = 1;
	}
	Token_alive = 1;
	E_queue( Memb_token_loss, 0, NULL, Token_timeout );
    	
	Last_token->type = 0;
	Last_token->seq  = 0;
	Last_token->aru  = 0;

	State = EVS;
	GlobalStatus.state = EVS;
}

void	Memb_print_form_token( sys_scatter *scat )
{
	token_header	*form_token;
	members_info	*m_info;
	reps_info	*r_info = NULL; /* avoids compile warning -- gcc not detect initialization */
        membership_id   *m_id_info = NULL; /* avoids compile warning -- gcc not detect initialization */
	ring_info	*rg_info;
	int32		*num_rings;
	int32		*commit_id;
	char		*c_ptr;
	int		num_bytes, bytes_to_skip;
	int		i,j, scat_index;
        int             is_form1 = 0;
        char            form_name[10];

	num_bytes  = 0;
        scat_index = 1;
	form_token = (token_header *)scat->elements[0].buf;

	m_info	   = (members_info *)&scat->elements[scat_index].buf[num_bytes];
	num_bytes  += sizeof(members_info);

        if (num_bytes == scat->elements[scat_index].len )
        {
            num_bytes = 0;
            scat_index++;
        }

        if ( Is_form1( form_token->type ) )
	{
            r_info	= (reps_info    *)&scat->elements[scat_index].buf[num_bytes];
            num_bytes  += sizeof(reps_info);
            is_form1 = 1;
	} else if( Is_form2( form_token->type ) )
        {
            m_id_info   = (membership_id *)&scat->elements[scat_index].buf[num_bytes];
            num_bytes  += sizeof(membership_id);
            is_form1 = 0;
        } else {
            Alarm( EXIT, "Invalid token type received: 0x%x\n", form_token->type);
            return;
        }

        if (num_bytes == scat->elements[scat_index].len )
        {
            num_bytes = 0;
            scat_index++;
        }
            
	num_rings  = (int32        *)&scat->elements[scat_index].buf[num_bytes];
	num_bytes  += sizeof(int32);

	rg_info= (ring_info    *)&scat->elements[scat_index].buf[num_bytes];

        /* Print form_token_header */

        Alarmp( SPLOG_PRINT, PRINT, "=========== Form Token ==========\n");

        if ( is_form1 )
            snprintf(&form_name[0], 10, "FORM 1");
        else 
            snprintf(&form_name[0], 10, "FORM 2");

        Alarmp( SPLOG_PRINT, PRINT, "%s Token, sent by %u.%u.%u.%u. Seq: %d\n", form_name, IP1(form_token->transmiter_id), IP2(form_token->transmiter_id), IP3(form_token->transmiter_id), IP4(form_token->transmiter_id), form_token->seq);
        Alarmp( SPLOG_PRINT, PRINT, "Configuration hash: %u (local hash %u)\n", form_token->conf_hash, Cn->hash_code);
        Alarmp( SPLOG_PRINT, PRINT, "ProcID: %u.%u.%u.%u\t ARU: %d, ARU LastID: %u.%u.%u.%u\n", IP1(form_token->proc_id), IP2(form_token->proc_id), IP3(form_token->proc_id), IP4(form_token->proc_id), form_token->aru, IP1(form_token->aru_last_id), IP2(form_token->aru_last_id), IP3(form_token->aru_last_id), IP4(form_token->aru_last_id) );
        Alarmp( SPLOG_PRINT, PRINT, "FlowControl: %hd\tRTR Len: %hd\n", form_token->flow_control, form_token->rtr_len);
        /* Print members list */

        Alarmp( SPLOG_PRINT, PRINT, "Form Token members list -- Active (%hd) Pending (%hd)\n", m_info->num_members, m_info->num_pending);
        for (i=0; i < m_info->num_members; i++) 
        {
            Alarmp( SPLOG_PRINT_NODATE, PRINT, "\t%u: %u.%u.%u.%u ", i, IP1(m_info->members[i]), IP2(m_info->members[i]), IP3(m_info->members[i]), IP4(m_info->members[i]) );
            if ( (i % 3) == 2 )
                Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");
        }

        Alarmp( SPLOG_PRINT_NODATE, PRINT, "\nPending Members:\n");

        for (i= m_info->num_members; i < ( m_info->num_members + m_info->num_pending); i++) 
        {
            Alarmp( SPLOG_PRINT_NODATE, PRINT, "\t%u: %u.%u.%u.%u ", i, IP1(m_info->members[i]), IP2(m_info->members[i]), IP3(m_info->members[i]), IP4(m_info->members[i]) );
            if ( (i % 3) == 2 )
                Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");
        }
        Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");

        if ( is_form1 )
        {
            /* Print reps list */
            Alarmp( SPLOG_PRINT, PRINT, "Form Token reps list -- Count (%hd) index (%hd)\n", r_info->num_reps, r_info->rep_index);
            for (i=0; i < r_info->num_reps; i++) 
            {
                Alarmp( SPLOG_PRINT_NODATE, PRINT, "\t%u: %u.%u.%u.%u (T %hd SegInd %hd) ", i, IP1(r_info->reps[i].proc_id), IP2(r_info->reps[i].proc_id), IP3(r_info->reps[i].proc_id), IP4(r_info->reps[i].proc_id), r_info->reps[i].type, r_info->reps[i].seg_index );
                if ( (i % 3) == 2 )
                    Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");
            }
            Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");
        } else  /* so is FORM2 type */ 
        {
            Alarmp( SPLOG_PRINT, PRINT, "Form Token Membership ID %u.%u.%u.%u : %d\n", IP1(m_id_info->proc_id), IP2(m_id_info->proc_id), IP3(m_id_info->proc_id), IP4(m_id_info->proc_id), m_id_info->time );
        }

        /* Print ring info */
        Alarmp( SPLOG_PRINT, PRINT, "Form Token RING list -- Count (%d)\n", *num_rings);
        for (i=0; i < *num_rings; i++) 
        {
            bytes_to_skip = sizeof(ring_info) + ( rg_info->num_holes + rg_info->num_commit ) * sizeof(int32);
            c_ptr = (char *) rg_info;

            Alarmp( SPLOG_PRINT, PRINT, "Ring %u: MembID %u.%u.%u.%u - %u\tTransTime %u\n", i, IP1(rg_info->memb_id.proc_id), IP2(rg_info->memb_id.proc_id), IP3(rg_info->memb_id.proc_id), IP4(rg_info->memb_id.proc_id), rg_info->memb_id.time, rg_info->trans_time);
            Alarmp( SPLOG_PRINT, PRINT, "\tARU: %d\tHighSeq: %d\tNumHoles: %d\n", rg_info->aru, rg_info->highest_seq, rg_info->num_holes);
            Alarmp( SPLOG_PRINT, PRINT, "\tNumCommit: %hd\tNumTrans: %hd\n", rg_info->num_commit, rg_info->num_trans);
            /* Now print all missing messages from this ring (holes) */
            commit_id = (int32 *) &c_ptr[sizeof(ring_info)];

            Alarmp( SPLOG_PRINT, PRINT, "\tMessage Holes:");
            for (j=0; j < rg_info->num_holes; j++) 
            {
                Alarmp( SPLOG_PRINT_NODATE, PRINT, "\t%u ", *commit_id);
                commit_id++;
            }
            Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");

            /* Now print transitional member list */
            Alarmp( SPLOG_PRINT, PRINT, "\tTrans List:");
            for (j=0; j < rg_info->num_trans; j++) 
            {
                Alarmp( SPLOG_PRINT_NODATE, PRINT, "\t%u: %u.%u.%u.%u ", j, IP1(*commit_id), IP2(*commit_id), IP3(*commit_id), IP4(*commit_id) );
                if ( (j % 3) == 2 )
                    Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");
                commit_id++;
            }
            Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");

            /* Now print commit list. This follows the trans list with no gaps. */
            Alarmp( SPLOG_PRINT, PRINT, "\tCommit List:");
            for (j=rg_info->num_trans; j < rg_info->num_commit; j++) 
            {
                Alarmp( SPLOG_PRINT_NODATE, PRINT, "\t%u: %u.%u.%u.%u ", j, IP1(*commit_id), IP2(*commit_id), IP3(*commit_id), IP4(*commit_id) );
                if ( (j % 3) == 2 )
                    Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");
                commit_id++;
            }
            Alarmp( SPLOG_PRINT_NODATE, PRINT, "\n");

            /* next ring */
	    rg_info = (ring_info *)&c_ptr[bytes_to_skip];
        }

        Alarmp( SPLOG_PRINT, PRINT, "====================================================\n");
}

static	void	Backoff_membership()
{
	int	pack_entry;
	int	i;

	pack_entry=-1;
	for( i=Last_discarded+1; i <= Highest_seq; i++ )
	{
		/* clear dummy messages */
		pack_entry = i & PACKET_MASK;
		if( Packets[pack_entry].exist == 3 )
			Packets[pack_entry].exist = 0;
	}

	/* return Aru and My_aru */
	Aru = Last_discarded;

	My_aru = Last_discarded;
	for( i=Last_discarded+1; i <= Highest_seq; i++ )
	{
		if( !Packets[pack_entry].exist ) break;
		My_aru++;
	}
}

void	Memb_commit()
{
	Commit_set = Future_commit_set;
}

void	Memb_transitional()
{
	int	i, j, k;
        int     num_seg, num_proc;
	int32u	proc_id;

	Alarm( MEMB, "Memb_transitional\n");

        num_seg = Conf_num_segments( Cn );

	Transitional = 1;
	Trans_membership.num_segments = num_seg;
	for( i=0; i < num_seg; i++ )
	{
                num_proc = Conf_num_procs_in_seg( Cn, i );
                Trans_membership.segments[i].num_procs = 0;
		for( j=0; j < num_proc; j++ )
		{
		    proc_id = Cn->segments[i].procs[j]->id;
		    for( k=0; k < Commit_set.num_pending; k++ )
		    {
			if( Commit_set.members[k] == proc_id )
			{
                                if ( Conf_append_id_to_seg( &Trans_membership.segments[i], proc_id) == -1)
                                        Alarm(EXIT, "Memb_transitional: Commit_set has member %u for trans who doesn't exist\n", proc_id);
				break;
			}
		    }
		}
	}

        Trans_memb_id.proc_id = Conf_leader( &Trans_membership );
        Trans_memb_id.time    = F_trans_memb_time;

	Commit_membership.num_segments = Conf_num_segments( Cn );
	for( i=0; i < num_seg; i++ )
	{
                num_proc = Conf_num_procs_in_seg( Cn, i );
		Commit_membership.segments[i].num_procs = 0;
		for( j=0; j < num_proc; j++ )
		{
		    proc_id = Cn->segments[i].procs[j]->id;
		    for( k=0; k < Commit_set.num_members; k++ )
		    {
			if( Commit_set.members[k] == proc_id )
			{
                                if ( Conf_append_id_to_seg(&Commit_membership.segments[i], proc_id) == -1)
                                        Alarm(EXIT, "Memb_transitional: Commit_set has member %u who doesn't exist\n", proc_id);
				break;
			}
		    }
		}
	}
}

void	Memb_regular()
{
	int	i;

	Alarm( MEMB, "Memb_regular\n");
	Transitional = 0;
	State = OP;
	GlobalStatus.state = OP;
	GlobalStatus.membership_changes++;
	Membership = Future_membership;
	Membership_id = Future_membership_id;
	Reg_membership = Membership;

	GlobalStatus.num_procs = 0;
	GlobalStatus.num_segments = 0;
	for( i=0; i < Membership.num_segments; i++ )
	{
		if( Membership.segments[i].num_procs > 0 )
		{
			GlobalStatus.num_procs += Membership.segments[i].num_procs;
			GlobalStatus.num_segments++;
		}
	}
	GlobalStatus.leader_id = Membership_id.proc_id;

	Foreign_found = 0;
	if( Conf_leader( &Membership ) == My.id )
		E_queue( Memb_lookup_new_members, 0, NULL, Lookup_timeout );
	printf("Membership id is ( %d, %d)\n", Membership_id.proc_id, Membership_id.time );
	printf("%c", Conf_print( &Membership ) );
}

void	Flip_members( members_info *members_ptr )
{
/*
 * This routine can not be called twice beacuse of num_members and num_pending
 */
	int	i;

	members_ptr->num_members = Flip_int16( members_ptr->num_members );
	members_ptr->num_pending = Flip_int16( members_ptr->num_pending );
	for( i=0; i < members_ptr->num_members + members_ptr->num_pending; i++ )
		members_ptr->members[i] = Flip_int32( members_ptr->members[i] );
}

void	Flip_reps( reps_info *reps_ptr )
{
/*
 * This routine can not be called twice beacuse of num_reps 
 */
	int	i;

	reps_ptr->num_reps  = Flip_int16( reps_ptr->num_reps );
	reps_ptr->rep_index = Flip_int16( reps_ptr->rep_index );
	for( i=0; i < reps_ptr->num_reps; i++ )
	{
	    reps_ptr->reps[i].proc_id	= Flip_int32( reps_ptr->reps[i].proc_id );
	    reps_ptr->reps[i].type	= Flip_int16( reps_ptr->reps[i].type );
	    reps_ptr->reps[i].seg_index = Flip_int16( reps_ptr->reps[i].seg_index );
	}
}

void	Flip_rings( char *buf )
{
/*
 * This routine can not be called twice beacuse of *num_rings
 * and of ring_info_ptr->num_holes
 */
	ring_info	*ring_info_ptr;
	int32		*num_rings;
	int		ptr;
	char		*c_ptr;
	int32		*seq_or_proc;
	int		i,j;

	c_ptr = buf;
	ptr = 0;
	num_rings = (int32 *)&c_ptr[ptr];

	*num_rings = Flip_int32( *num_rings );
	ptr += sizeof(int32);

	for( i=0; i < *num_rings; i++ )
	{
	    ring_info_ptr = (ring_info *)&c_ptr[ptr];

	    ring_info_ptr->memb_id.proc_id = Flip_int32( ring_info_ptr->memb_id.proc_id );
	    ring_info_ptr->memb_id.time    = Flip_int32( ring_info_ptr->memb_id.time );
            ring_info_ptr->trans_time      = Flip_int32( ring_info_ptr->trans_time );
	    ring_info_ptr->aru		   = Flip_int32( ring_info_ptr->aru );
	    ring_info_ptr->highest_seq	   = Flip_int32( ring_info_ptr->highest_seq );
	    ring_info_ptr->num_holes	   = Flip_int32( ring_info_ptr->num_holes );
	    ring_info_ptr->num_commit	   = Flip_int16( ring_info_ptr->num_commit );
	    ring_info_ptr->num_trans	   = Flip_int16( ring_info_ptr->num_trans );

	    ptr += sizeof(ring_info);

	    for( j=0; j < ( ring_info_ptr->num_holes + ring_info_ptr->num_commit ); j++ )
	    {
		seq_or_proc = (int32 *)&c_ptr[ptr];
		*seq_or_proc = Flip_int32( *seq_or_proc );
		ptr += sizeof(int32);
	    }
	}
}
